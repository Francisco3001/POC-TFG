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

    @GetMapping
    public List<User> getUsers() {
        return userRepository.findAll();
    }

        @GetMapping("/search")
    public List<User> search(@RequestParam String username) {

        String sql = "SELECT * FROM users WHERE username = '" + username + "'";

        return entityManager
                .createNativeQuery(sql, User.class)
                .getResultList();
    }
    @GetMapping("/file")
    public String readFile(@RequestParam String filename) throws IOException {

        Path path = Paths.get("uploads/" + filename);

        return Files.readString(path);
    }
    
    @GetMapping("/config")
    public Map<String, String> config() {

        Map<String, String> config = new HashMap<>();

        config.put("dbUser", "postgres");
        config.put("dbPassword", "postgres123");
        config.put("jwtSecret", "my-super-secret-key");

        return config;
    }

}
