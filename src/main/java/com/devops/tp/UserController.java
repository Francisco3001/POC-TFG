package com.devops.tp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;

import java.util.List;

@RestController
@RequestMapping("/users")
public class UserController {

    @Autowired
    private UserRepository userRepository;
    @PersistenceContext
    private EntityManager entityManager;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User createUser(@RequestBody User user) {
        return userRepository.save(user);
    }
    
    @GetMapping("/search")
    public String searchUser(@RequestParam String username) {
        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement()) {

            String query = "SELECT * FROM users WHERE username = '" + username + "'";
            ResultSet rs = stmt.executeQuery(query);

            StringBuilder result = new StringBuilder();
            while (rs.next()) {
                result.append(rs.getString("username")).append("\n");
            }

            return result.toString();

        } catch (Exception e) {
            return e.getMessage();
        }
    }

    @GetMapping
    public List<User> getUsers() {
        return userRepository.findAll();
    }
}
